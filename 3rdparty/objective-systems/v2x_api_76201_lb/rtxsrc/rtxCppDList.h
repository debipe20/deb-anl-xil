/*
 * Copyright (c) 2003-2022 Objective Systems, Inc.
 *
 * This software is furnished under a license and may be used and copied
 * only in accordance with the terms of such license and with the
 * inclusion of the above copyright notice. This software or any other
 * copies thereof may not be provided or otherwise made available to any
 * other person. No title to and ownership of the software is hereby
 * transferred.
 *
 * The information in this software is subject to change without notice
 * and should not be construed as a commitment by Objective Systems, Inc.
 *
 * PROPRIETARY NOTICE
 *
 * This software is an unpublished work subject to a confidentiality agreement
 * and is protected by copyright and trade secret law.  Unauthorized copying,
 * redistribution or other use of this work is prohibited.
 *
 * The above notice of copyright on this source code product does not indicate
 * any actual or intended publication of such source code.
 *
 *****************************************************************************/
/**
 * @file rtxCppDList.h
 */
#ifndef _RTXCPPDLIST_H_
#define _RTXCPPDLIST_H_

#include "rtxsrc/OSRTBaseType.h"
#include "rtxsrc/rtxDList.h"

/**
 * This class is a base class for C++ representations of a node for the
 * doubly-linked list structure.  It extends the C OSRTDListNode type.
 */
class EXTRTCLASS OSRTDListNodeBaseClass : protected OSRTDListNode {
   friend class OSRTDListBaseClass;
   friend class OSRTDListClass;
   friend class OSRTObjListClass;
 protected:
   inline operator OSRTDListNode* () { return this; }
   inline operator const OSRTDListNode* () const { return this; }

   OSRTDListNodeBaseClass ();
 public:
   OSRTDListNodeBaseClass (void* pdata);
   virtual ~OSRTDListNodeBaseClass() {}
} ;

/**
 * This class represents a doubly-linked list node structure.  It extends the
 * C++ \c OSRTDListNodeBaseClass type.
 */
class EXTRTCLASS OSRTDListNodeClass : public OSRTDListNodeBaseClass {
 public:
   inline OSRTDListNodeClass (void* pdata) :
      OSRTDListNodeBaseClass (pdata) {}
   virtual ~OSRTDListNodeClass();

   /**
    * This method returns a pointer to a data associated with the node.
    *
    * @return     Node data pointer.
    */
   inline void* getData () { return data; }

   /**
    * This method returns a pointer to a data associated with the node.
    *
    * @return     Node data pointer.
    */
   inline const void* getData () const { return data; }

   /**
    * This method returns a pointer to a next node in the list.
    *
    * @return     Pointer to the next node.
    */
   inline OSRTDListNodeClass* getNext () {
      return (OSRTDListNodeClass*)next;
   }

   /**
    * This method returns a pointer to a next node in the list.
    *
    * @return     Pointer to the next node.
    */
   inline const OSRTDListNodeClass* getNext () const {
      return (OSRTDListNodeClass*)next;
   }

   /**
    * This method returns a pointer to a previous node in the list.
    *
    * @return     Pointer to the previous node.
    */
   inline OSRTDListNodeClass* getPrev () {
      return (OSRTDListNodeClass*)prev;
   }

   /**
    * This method returns a pointer to a previous node in the list.
    *
    * @return     Pointer to the previous node.
    */
   inline const OSRTDListNodeClass* getPrev () const {
      return (OSRTDListNodeClass*)prev;
   }
} ;

/**
 * This class represents a doubly-linked list node structure for \c OSRTBaseType
 * instances.  It extends the C++ \c OSRTDListNodeBaseClass type.
 */
class EXTRTCLASS OSRTObjListNodeClass : public OSRTDListNodeBaseClass {
 public:
   OSRTObjListNodeClass (OSRTBaseType* pdata);
   OSRTObjListNodeClass (const OSRTObjListNodeClass&);
   virtual ~OSRTObjListNodeClass();

   /**
    * This method returns a pointer to a data associated with the node.
    *
    * @return     Node data pointer.
    */
   inline OSRTBaseType* getData () { return (OSRTBaseType*)data; }

   /**
    * This method returns a pointer to a data associated with the node.
    *
    * @return     Node data pointer.
    */
   inline const OSRTBaseType* getData () const { return (OSRTBaseType*)data; }

   /**
    * This method returns a pointer to a next node in the list.
    *
    * @return     Pointer to the next node.
    */
   inline OSRTObjListNodeClass* getNext () {
      return (OSRTObjListNodeClass*)next;
   }

   /**
    * This method returns a pointer to a next node in the list.
    *
    * @return     Pointer to the next node.
    */
   inline const OSRTObjListNodeClass* getNext () const {
      return (OSRTObjListNodeClass*)next;
   }

   /**
    * This method returns a pointer to a previous node in the list.
    *
    * @return     Pointer to the previous node.
    */
   inline OSRTObjListNodeClass* getPrev () {
      return (OSRTObjListNodeClass*)prev;
   }

   /**
    * This method returns a pointer to a previous node in the list.
    *
    * @return     Pointer to the previous node.
    */
   inline const OSRTObjListNodeClass* getPrev () const {
      return (OSRTObjListNodeClass*)prev;
   }
} ;

/**
 * This class is a base class for C++ representations of a doubly-linked
 * list classes. It is derived from the OSRTBaseType class as well as the C
 * OSRTDList structure. This class provides a basic functionality for
 * C++ doubly-linked list.
 */
class EXTRTCLASS OSRTDListBaseClass : public OSRTDList, public OSRTBaseType {
 protected:
   inline OSRTDListBaseClass(const OSRTDListBaseClass& o):OSRTBaseType (o) {}

 public:
   inline operator OSRTDList* () { return this; }
   inline operator const OSRTDList* () const { return this; }

   /**
    * The default constructor initializes the list contents to empty.
    */
   inline OSRTDListBaseClass() { count = 0; head = 0; tail = 0; }

   /**
    * The destructor will delete all the nodes in the list.
    */
   virtual ~OSRTDListBaseClass();

   /**
    * This method returns count of items in the list.
    *
    * @return - Count of items in the list
    */
   inline OSSIZE getCount () const { return count; }

   /**
    * This method returns a pointer to OSRTDList structure for the
    * list instance.
    *
    * @return - a pointer to OSRTDList structure for the
    * list instance.
    */
   inline OSRTDList* getList () { return this; }

   /**
    * This method returns a const pointer to OSRTDList structure for the
    * list instance.
    *
    * @return - a const pointer to OSRTDList structure for the
    * list instance.
    */
   inline const OSRTDList* getList () const { return this; }

   /**
    * The remove method removes the data item at the given index
    * from the list.  The index is zero-based.
    *
    * @param index - Zero-based index of item to be removed.
    */
   void remove (int index);

   void release ();
} ;

/**
 * This class represents a doubly-linked list structure.  It extends the
 * C++ \c OSRTDListBaseClass type. It provides methods for adding,
 * retrieving, and removing items from linked lists. This list class is used
 * to hold primitive types which are NOT derived from OSRTBaseType.
 * See description of \c OSRTObjListClass for list of objects class.
 */
class EXTRTCLASS OSRTDListClass : public OSRTDListBaseClass {
 public:
   /**
    * The default constructor initializes the list contents to empty.
    */
   OSRTDListClass() {}

   /**
    * The copy constructor makes a copy of the list object.
    */
   OSRTDListClass (const OSRTDListClass& o) : OSRTDListBaseClass(o) {}

   /**
    * The append method adds an item to the end of the list.
    *
    * @param pdata     - Pointer to data item to be appended to list.  Note
    *                    the pointer itself is appended - a copy is not made.
    */
   void append (void* pdata);

   /**
    * The appendCopy method adds a copy of an item to the end of the list.
    *
    * @param pdata     - Pointer to data item to be appended to list.  Note
    *                    that clone() is called on the data item, and the
    *                    returned copy is stored in the list.
    * @param nbytes    - Size of the data pointed to in bytes.
   */
   void appendCopy (void* pdata, size_t nbytes);

   /**
    * This method returns a pointer to a head node of the list.
    *
    * @return          - Pointer to head node.
    */
   inline OSRTDListNodeClass* getHead () {
      return (OSRTDListNodeClass*)head;
   }

   /**
    * This method returns a pointer to a head node of the list.
    *
    * @return          - Pointer to head node.
    */
   inline const OSRTDListNodeClass* getHead () const {
      return (OSRTDListNodeClass*)head;
   }

   /**
    * The getItem method retrieves the data item from the list at the
    * given index.  The index is zero-based.
    *
    * @param idx - Zero-based index of the node to retrieve.
    * @return - Pointer to node structure containing the indexed data item.
    */
   inline const void* getItem (int idx) const {
      OSRTDListNodeClass* pnode =
         (OSRTDListNodeClass*) rtxDListFindByIndex (*this, idx);
      return (0 != pnode) ? pnode->getData () : 0;
   }

   /**
    * This method returns a pointer to a tail node of the list.
    *
    * @return          - Pointer to tail node.
    */
   inline OSRTDListNodeClass* getTail () {
      return (OSRTDListNodeClass*)tail;
   }

   /**
    * This method returns a pointer to a tail node of the list.
    *
    * @return          - Pointer to tail node.
    */
   inline const OSRTDListNodeClass* getTail () const {
      return (OSRTDListNodeClass*)tail;
   }

   /**
    * The insert method inserts a data item into the list at the given
    * indexed location.  The index is zero-based.
    *
    * @param index - Zero-based index of insertion point.
    * @param pdata - Pointer to data item to be inserted into list.  Note
    *                the pointer itself is inserted - a copy is not made.
    */
   void insert (int index, void* pdata);

} ;

/**
 * This class represents a doubly-linked list structure for objects.
 * It extends the C++ \c OSRTDListBaseClass type. It is similar to the
 * \c OSRTDListClass described above except that the base type for items in
 * the list is \c OSRTBaseType. This allows items in the list to be properly
 * destructed when memory ownership for the items is transferred to the list
 * object.
 */
class EXTRTCLASS OSRTObjListClass : public OSRTDListBaseClass {
 protected:
    void doCopy (const OSRTObjListClass&);
 public:

   /**
    * The default constructor initializes the list contents to empty.
    */
   inline OSRTObjListClass() { }

   OSRTObjListClass(const OSRTObjListClass&);

   /**
    * The append method adds an item to the end of the list.
    *
    * @param pdata     - Pointer to data item to be appended to list.  Note
    *                    the pointer itself is appended - a copy is not made.
    */
   void append (OSRTBaseType* pdata);

   /**
    * The appendCopy method adds a copy of an item to the end of the list.
    *
    * @param pdata     - Pointer to data item to be appended to list.  Note
    *                    that clone() is called on the data item, and the
    *                    returned copy is stored in the list.
   */
   void appendCopy (const OSRTBaseType* pdata);

   OSRTBaseType* clone () const { return new OSRTObjListClass (*this); }

   /**
    * This method returns a pointer to a head node of the list.
    *
    * @return          - Pointer to head node.
    */
   inline OSRTObjListNodeClass* getHead () {
      return (OSRTObjListNodeClass*)head;
   }

   /**
    * This method returns a pointer to a head node of the list.
    *
    * @return          - Pointer to head node.
    */
   inline const OSRTObjListNodeClass* getHead () const {
      return (OSRTObjListNodeClass*)head;
   }

   /**
    * The getItem method retrieves the data item from the list at the
    * given index.  The index is zero-based.
    *
    * @param idx - Zero-based index of the node to retrieve.
    * @return - Pointer to node structure containing the indexed data item.
    */
   inline const OSRTBaseType* getItem (int idx) const {
      OSRTObjListNodeClass* pnode =
         (OSRTObjListNodeClass*) rtxDListFindByIndex (*this, idx);
      return (0 != pnode) ? (OSRTBaseType*)pnode->getData () : 0;
   }

   /**
    * This method returns a pointer to a tail node of the list.
    *
    * @return          - Pointer to tail node.
    */
   inline OSRTObjListNodeClass* getTail () {
      return (OSRTObjListNodeClass*)tail;
   }

   /**
    * This method returns a pointer to a tail node of the list.
    *
    * @return          - Pointer to tail node.
    */
   inline const OSRTObjListNodeClass* getTail () const {
      return (OSRTObjListNodeClass*)tail;
   }

   /**
    * The insert method inserts a data item into the list at the given
    * indexed location.  The index is zero-based.
    *
    * @param index - Zero-based index of insertion point.
    * @param pdata - Pointer to data item to be inserted into list.  Note
    *                the pointer itself is inserted - a copy is not made.
    */
   void insert (int index, OSRTBaseType* pdata);

   /**
    * Assignment operator.
    *
    * Sets the list's value to the value of the given list.  Note that
    * a copy of each object in the given list is made.
    */
   OSRTObjListClass& operator= (const OSRTObjListClass&);
} ;
#endif
